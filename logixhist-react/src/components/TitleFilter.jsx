import '../assets/styles/list-groups.css'
import '../assets/styles/bootstrap.min.css';

function TitleFilter() {
  return(
    <div>
      <div className="list-group-title">
          <a href="#" className="list-group-item list-group-item-action d-flex gap-3 py-3" aria-current="true">
            <img src="https://github.com/twbs.png" alt="twbs" width="32" height="32" className="rounded-circle flex-shrink-0"/>
            <div className="d-flex gap-2 w-100 justify-content-between">
              <div>
                <h6 className="mb-0">here</h6>
              </div>
            </div>
          </a>
        </div>
    </div>
  );
}

export default TitleFilter;