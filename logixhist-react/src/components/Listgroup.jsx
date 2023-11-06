import TitleFilter from "./TitleFilter";
import '../assets/styles/list-groups.css';
import '../assets/styles/bootstrap.min.css';
 
function Listgroup({items}) {
  return(
    <div className="list-group-box">
      <TitleFilter></TitleFilter>
      <div className="list-group">
        {items.map((item, index) => (
          <div key={index}>
            <a href="#" className="list-group-item list-group-item-action d-flex gap-3 py-3" aria-current="true">
              <img src="https://github.com/twbs.png" alt="twbs" width="32" height="32" className="rounded-circle flex-shrink-0"/>
            <div className="d-flex gap-2 w-100 justify-content-between">
                <div>
                  <h6>{item}</h6>
                </div>
              </div>
            </a>
          </div>
        ))}
      </div>
    </div>

    // <div className="list-group-box">
    //   {items.map((item, index) => (
    //     <div className="list-group">
    //       <a href="#" className="list-group-item list-group-item-action d-flex gap-3 py-3" aria-current="true">
    //         <img src="https://github.com/twbs.png" alt="twbs" width="32" height="32" className="rounded-circle flex-shrink-0"/>
    //         <div className="d-flex gap-2 w-100 justify-content-between">
    //           <div>
    //             <h6>{item}</h6>
    //           </div>
    //         </div>
    //       </a>
    //     </div>
    //   ))}
    // </div>
  );
}

export default Listgroup;